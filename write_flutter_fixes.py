import os

SEARCH_SCREEN_DART = '''import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/providers/journey_providers.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});
  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _fromController = TextEditingController(text: 'MDU');
  final TextEditingController _toController = TextEditingController(text: 'SBC');
  DateTime _selectedDate = DateTime.now();
  String _selectedMode = 'DEFAULT';
  bool _isLoading = false;

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_isLoading) return;

    setState(() => _isLoading = true);

    ref.read(searchParamsProvider.notifier).state = {
      'from': _fromController.text,
      'to': _toController.text,
      'date': "${_selectedDate.year}-${_selectedDate.month.toString().padLeft(2, '0')}-${_selectedDate.day.toString().padLeft(2, '0')}",
      'mode': _selectedMode,
    };

    // Pre-fetch or just let the results screen do it. 
    // Tapping push will let results screen build and trigger watch.
    setState(() => _isLoading = false);
    context.push('/results');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar.large(title: const Text('NextRoute')),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            TextFormField(
                              controller: _fromController,
                              decoration: const InputDecoration(labelText: 'Leaving from', prefixIcon: Icon(Icons.trip_origin)),
                              validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                            ),
                            IconButton(
                              icon: const Icon(Icons.swap_vert),
                              onPressed: () {
                                final temp = _fromController.text;
                                _fromController.text = _toController.text;
                                _toController.text = temp;
                              },
                            ),
                            TextFormField(
                              controller: _toController,
                              decoration: const InputDecoration(labelText: 'Going to', prefixIcon: Icon(Icons.location_on)),
                              validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                            ),
                            const SizedBox(height: 16),
                            InkWell(
                              onTap: () async {
                                final date = await showDatePicker(
                                  context: context,
                                  initialDate: _selectedDate,
                                  firstDate: DateTime.now(),
                                  lastDate: DateTime.now().add(const Duration(days: 90)),
                                );
                                if (date != null) setState(() => _selectedDate = date);
                              },
                              child: InputDecorator(
                                decoration: const InputDecoration(labelText: 'Date of Travel', prefixIcon: Icon(Icons.calendar_today)),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text("${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}"),
                                    const Icon(Icons.arrow_drop_down),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 32),
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: FilledButton.icon(
                        onPressed: _isLoading ? null : _submit,
                        icon: _isLoading ? const CircularProgressIndicator(color: Colors.white) : const Icon(Icons.search),
                        label: Text(_isLoading ? 'Searching...' : 'Find Routes'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
'''

RESULTS_SCREEN_DART = '''import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/providers/journey_providers.dart';

class ResultsScreen extends ConsumerWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResults = ref.watch(searchResultsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Available Routes')),
      body: asyncResults.when(
        data: (journeys) {
          if (journeys.isEmpty) {
            return const Center(child: Text("No routes found. Try nearby stations."));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: journeys.length,
            itemBuilder: (context, index) {
              final j = journeys[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 16),
                child: InkWell(
                  onTap: () => context.push('/journey_detail/${j.journeyId}'),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Score: ${j.overallScore.toStringAsFixed(1)}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                        const SizedBox(height: 8),
                        Text('${j.totalTransfers} Transfers | ${j.totalDurationMins} mins | ₹${j.totalCost}'),
                      ],
                    ),
                  ),
                ),
              );
            },
          );
        },
        loading: () => ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: 3,
          itemBuilder: (context, index) => const Card(
            child: SizedBox(height: 100, child: Center(child: CircularProgressIndicator())),
          ),
        ),
        error: (err, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error, color: Colors.red, size: 48),
              const SizedBox(height: 16),
              const Text("Failed to load routes."),
              TextButton(onPressed: () => ref.refresh(searchResultsProvider), child: const Text("Retry"))
            ],
          )
        ),
      ),
    );
  }
}
'''

JOURNEY_DETAIL_SCREEN_DART = '''import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/providers/journey_providers.dart';

class JourneyDetailScreen extends ConsumerWidget {
  final String journeyId;
  const JourneyDetailScreen({super.key, required this.journeyId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncResults = ref.watch(searchResultsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Journey Timeline')),
      body: asyncResults.when(
        data: (journeys) {
          final journey = journeys.where((j) => j.journeyId == journeyId).firstOrNull;
          if (journey == null) return const Center(child: Text("Journey not found."));

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: journey.segments.map((s) {
                final isWalk = s.segmentType == 'WALK';
                final isNextDay = s.arrivalTime.day > s.departureTime.day;
                
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Column(
                        children: [
                          Icon(isWalk ? Icons.directions_walk : Icons.train, color: isWalk ? Colors.grey : Colors.blue),
                          Container(
                            height: 40, width: 2, 
                            color: isWalk ? Colors.transparent : Colors.grey,
                            child: isWalk ? const VerticalDivider(color: Colors.grey, thickness: 2, width: 2) : null,
                          ),
                        ],
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(child: Text(s.origin.name, style: const TextStyle(fontWeight: FontWeight.bold))),
                                Text("${s.departureTime.hour.toString().padLeft(2,'0')}:${s.departureTime.minute.toString().padLeft(2,'0')}"),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(isWalk ? "Walk ${s.durationMins} mins" : "${s.vehicleName} (${s.vehicleNumber})", style: TextStyle(color: Colors.grey[600])),
                            if (isNextDay)
                              const Text("+1 Day", style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 12)),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, s) => const Center(child: Text("Failed to load journey details.")),
      ),
    );
  }
}
'''

ROUTER_DART = '''import 'package:go_router/go_router.dart';
import '../features/search/presentation/search_screen.dart';
import '../features/results/presentation/results_screen.dart';
import '../features/journey_detail/presentation/journey_detail_screen.dart';

final goRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const SearchScreen(),
    ),
    GoRoute(
      path: '/results',
      builder: (context, state) => const ResultsScreen(),
    ),
    GoRoute(
      path: '/journey_detail/:id',
      builder: (context, state) => JourneyDetailScreen(journeyId: state.pathParameters['id']!),
    ),
  ],
);
'''

def write_flutter():
    with open('frontend/lib/features/search/presentation/search_screen.dart', 'w', encoding='utf-8') as f:
        f.write(SEARCH_SCREEN_DART)
    with open('frontend/lib/features/results/presentation/results_screen.dart', 'w', encoding='utf-8') as f:
        f.write(RESULTS_SCREEN_DART)
    with open('frontend/lib/features/journey_detail/presentation/journey_detail_screen.dart', 'w', encoding='utf-8') as f:
        f.write(JOURNEY_DETAIL_SCREEN_DART)
    with open('frontend/lib/app/router.dart', 'w', encoding='utf-8') as f:
        f.write(ROUTER_DART)
    print("Flutter UX fixes applied.")

if __name__ == "__main__":
    write_flutter()
