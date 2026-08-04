import os

SEARCH_SCREEN = '''import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  final TextEditingController _fromController = TextEditingController();
  final TextEditingController _toController = TextEditingController();
  DateTime _selectedDate = DateTime.now();
  String _selectedMode = 'DEFAULT';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar.large(
            title: const Text('NextRoute'),
            actions: [
              IconButton(icon: const Icon(Icons.settings), onPressed: () {}),
            ],
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Card(
                    elevation: 2,
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          TextField(
                            controller: _fromController,
                            decoration: InputDecoration(
                              labelText: 'Leaving from',
                              prefixIcon: const Icon(Icons.trip_origin),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 8.0),
                            child: Row(
                              children: [
                                const Expanded(child: Divider()),
                                IconButton(
                                  icon: const Icon(Icons.swap_vert),
                                  onPressed: () {
                                    final temp = _fromController.text;
                                    _fromController.text = _toController.text;
                                    _toController.text = temp;
                                  },
                                ),
                                const Expanded(child: Divider()),
                              ],
                            ),
                          ),
                          TextField(
                            controller: _toController,
                            decoration: InputDecoration(
                              labelText: 'Going to',
                              prefixIcon: const Icon(Icons.location_on),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                            ),
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
                              decoration: InputDecoration(
                                labelText: 'Date of Travel',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                prefixIcon: const Icon(Icons.calendar_today),
                              ),
                              child: Text(
                                "${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}",
                                style: theme.textTheme.titleMedium,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text('Travel Mode', style: theme.textTheme.titleMedium),
                  const SizedBox(height: 8),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: ['DEFAULT', 'WOMEN', 'SENIOR', 'STUDENT'].map((mode) {
                        final isSelected = _selectedMode == mode;
                        return Padding(
                          padding: const EdgeInsets.only(right: 8.0),
                          child: FilterChip(
                            label: Text(mode),
                            selected: isSelected,
                            onSelected: (val) => setState(() => _selectedMode = mode),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: FilledButton.icon(
                      onPressed: () {
                        // Pass mock data or simple params
                        context.push('/results');
                      },
                      icon: const Icon(Icons.search),
                      label: const Text('Find Routes', style: TextStyle(fontSize: 18)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
'''

RESULTS_SCREEN = '''import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ResultsScreen extends ConsumerWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Available Routes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () => _showFilterBottomSheet(context),
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 5,
        itemBuilder: (context, index) {
          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            clipBehavior: Clip.antiAlias,
            child: InkWell(
              onTap: () => context.push('/journey_detail'),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Chip(label: Text('Best Overall'), backgroundColor: Colors.greenAccent),
                        Text('Score: ${95 - index}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        const Icon(Icons.train, color: Colors.blue),
                        const SizedBox(width: 8),
                        const Text('20:00 MDU'),
                        const Expanded(child: Divider(indent: 8, endIndent: 8)),
                        const Text('5h 30m'),
                        const Expanded(child: Divider(indent: 8, endIndent: 8)),
                        const Text('01:30 SBC'),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('1 Transfer', style: TextStyle(color: Colors.orange)),
                        Text('₹1,250', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      ],
                    )
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  void _showFilterBottomSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Sort By', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: ['Score', 'Duration', 'Price', 'Transfers'].map((e) => ChoiceChip(label: Text(e), selected: e == 'Score')).toList(),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: FilledButton(onPressed: () => context.pop(), child: const Text('Apply')),
            )
          ],
        ),
      ),
    );
  }
}
'''

JOURNEY_DETAIL_SCREEN = '''import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class JourneyDetailScreen extends ConsumerWidget {
  const JourneyDetailScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Journey Timeline'),
        actions: [
          IconButton(icon: const Icon(Icons.map), onPressed: () => context.push('/map')),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildTimelineItem(context, 'Madurai Junction (MDU)', '20:00', 'Train 12638 - Pandian SF', Icons.train),
            _buildTransferItem(context, '1h 30m buffer'),
            _buildTimelineItem(context, 'Chennai Egmore (MS)', '04:30', 'Walk 500m', Icons.directions_walk),
            _buildTransferItem(context, '30m buffer'),
            _buildTimelineItem(context, 'Chennai Central (MAS)', '05:00', 'Train 12027 - Shatabdi', Icons.train),
            _buildTimelineItem(context, 'KSR Bengaluru (SBC)', '10:00', 'Arrive', Icons.location_on),
            
            const SizedBox(height: 24),
            Text('Journey Insights', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            Card(
              child: ListTile(
                leading: const Icon(Icons.security, color: Colors.green),
                title: const Text('Safest Route'),
                subtitle: const Text('Avoids late night transfers and uses major stations.'),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.money_off, color: Colors.blue),
                title: const Text('Budget Friendly'),
                subtitle: const Text('Total Cost: ₹1,250'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineItem(BuildContext context, String station, String time, String desc, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            children: [
              Icon(icon, color: Theme.of(context).colorScheme.primary),
              Container(height: 40, width: 2, color: Colors.grey.withOpacity(0.5)),
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
                    Text(station, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Text(time, style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 4),
                Text(desc, style: TextStyle(color: Colors.grey[600])),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransferItem(BuildContext context, String text) {
    return Padding(
      padding: const EdgeInsets.only(left: 12, bottom: 8),
      child: Row(
        children: [
          const Icon(Icons.timer, size: 16, color: Colors.orange),
          const SizedBox(width: 24),
          Text(text, style: const TextStyle(color: Colors.orange, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
'''

MAP_SCREEN = '''import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapScreen extends StatelessWidget {
  const MapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Route Map')),
      body: FlutterMap(
        options: const MapOptions(
          initialCenter: LatLng(10.8505, 76.2711), // Kerala/TN center
          initialZoom: 6,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.nextroute.app',
          ),
          PolylineLayer(
            polylines: [
              Polyline(
                points: const [
                  LatLng(9.9252, 78.1198), // MDU
                  LatLng(13.0827, 80.2707), // MAS
                  LatLng(12.9770, 77.5730), // SBC
                ],
                color: Theme.of(context).colorScheme.primary,
                strokeWidth: 4.0,
              ),
            ],
          ),
          MarkerLayer(
            markers: [
              Marker(
                point: const LatLng(9.9252, 78.1198),
                child: const Icon(Icons.location_on, color: Colors.red, size: 40),
              ),
              Marker(
                point: const LatLng(13.0827, 80.2707),
                child: const Icon(Icons.change_circle, color: Colors.orange, size: 30),
              ),
              Marker(
                point: const LatLng(12.9770, 77.5730),
                child: const Icon(Icons.location_on, color: Colors.green, size: 40),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
'''

APP_ROUTER = '''import 'package:go_router/go_router.dart';
import '../features/search/presentation/search_screen.dart';
import '../features/results/presentation/results_screen.dart';
import '../features/journey_detail/presentation/journey_detail_screen.dart';
import '../features/map/presentation/map_screen.dart';

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
      path: '/journey_detail',
      builder: (context, state) => const JourneyDetailScreen(),
    ),
    GoRoute(
      path: '/map',
      builder: (context, state) => const MapScreen(),
    ),
  ],
);
'''

def write_files():
    with open("lib/features/search/presentation/search_screen.dart", "w", encoding="utf-8") as f: f.write(SEARCH_SCREEN)
    with open("lib/features/results/presentation/results_screen.dart", "w", encoding="utf-8") as f: f.write(RESULTS_SCREEN)
    with open("lib/features/journey_detail/presentation/journey_detail_screen.dart", "w", encoding="utf-8") as f: f.write(JOURNEY_DETAIL_SCREEN)
    with open("lib/features/map/presentation/map_screen.dart", "w", encoding="utf-8") as f: f.write(MAP_SCREEN)
    with open("lib/app/router.dart", "w", encoding="utf-8") as f: f.write(APP_ROUTER)
    print("Frontend UI implemented.")

if __name__ == "__main__":
    write_files()
