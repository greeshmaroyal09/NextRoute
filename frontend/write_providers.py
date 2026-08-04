import os

REPOSITORIES = '''import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../shared/domain/models/models.dart';

final apiClientProvider = Provider((ref) => ApiClient());

final journeyRepositoryProvider = Provider((ref) => JourneyRepository(ref.read(apiClientProvider)));

class JourneyRepository {
  final ApiClient _api;
  JourneyRepository(this._api);

  Future<List<JourneyResponse>> searchRoutes(String from, String to, String date, String mode) async {
    final response = await _api.post('/search/routes', data: {
      'from_code': from,
      'to_code': to,
      'date': date,
      'mode': mode
    });
    final List journeys = response.data['journeys'];
    return journeys.map((e) => JourneyResponse.fromJson(e)).toList();
  }
}
'''

PROVIDERS = '''import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/repositories.dart';
import '../../shared/domain/models/models.dart';

final searchParamsProvider = StateProvider<Map<String, String>>((ref) => {
  'from': 'MDU',
  'to': 'SBC',
  'date': '2026-08-05',
  'mode': 'DEFAULT'
});

final searchResultsProvider = FutureProvider<List<JourneyResponse>>((ref) async {
  final params = ref.watch(searchParamsProvider);
  final repo = ref.watch(journeyRepositoryProvider);
  return await repo.searchRoutes(params['from']!, params['to']!, params['date']!, params['mode']!);
});
'''

def write_providers():
    os.makedirs('lib/shared/data', exist_ok=True)
    os.makedirs('lib/shared/providers', exist_ok=True)
    
    with open('lib/shared/data/repositories.dart', 'w', encoding='utf-8') as f:
        f.write(REPOSITORIES)
        
    with open('lib/shared/providers/journey_providers.dart', 'w', encoding='utf-8') as f:
        f.write(PROVIDERS)
        
    print("Repositories and Providers written.")

if __name__ == '__main__':
    write_providers()
