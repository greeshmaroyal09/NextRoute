import os

FLUTTER_PROVIDERS = '''import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'dart:convert';
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
  final box = Hive.box('history');
  final cacheKey = "${params['from']}-${params['to']}-${params['date']}-${params['mode']}";
  
  try {
    final results = await repo.searchRoutes(params['from']!, params['to']!, params['date']!, params['mode']!);
    
    // Save to Hive for offline fallback
    box.put(cacheKey, jsonEncode(results.map((e) => {
        'journey_id': e.journeyId,
        'total_duration_mins': e.totalDurationMins,
        'total_cost': {'total_fare': e.totalCost},
        'total_transfers': e.totalTransfers,
        'score': {'overall_score': e.overallScore},
        'badges': e.badges,
        'recommendation_sentence': e.recommendationSentence,
        'segments': e.segments.map((s) => {
            'segment_type': s.segmentType,
            'origin': {'code': s.origin.code, 'name': s.origin.name, 'type': s.origin.type},
            'destination': {'code': s.destination.code, 'name': s.destination.name, 'type': s.destination.type},
            'departure_time': s.departureTime,
            'arrival_time': s.arrivalTime,
            'duration_mins': s.durationMins,
            'distance_km': s.distanceKm,
            'vehicle_info': {'name': s.vehicleName},
            'cost': {'total_fare': s.totalFare}
        }).toList()
    }).toList()));
    
    return results;
  } on DioException catch (e) {
    // OFFLINE FALLBACK
    final cachedData = box.get(cacheKey);
    if (cachedData != null) {
      final List decoded = jsonDecode(cachedData);
      return decoded.map((e) => JourneyResponse.fromJson(e)).toList();
    }
    rethrow;
  }
});
'''

def write_flutter():
    with open('frontend/lib/shared/providers/journey_providers.dart', 'w', encoding='utf-8') as f:
        f.write(FLUTTER_PROVIDERS)
    print("Flutter offline fallback implemented.")

if __name__ == "__main__":
    write_flutter()
