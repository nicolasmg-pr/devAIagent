import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../repositories/stats_repository.dart';
import '../entities/stat_entities.dart';

class GetMonthlyStatsUseCase {
  final StatsRepository _repository;

  GetMonthlyStatsUseCase(this._repository);

  Future<Either<Failure, StatsResponse>> call({
    int? month,
    int? year,
  }) async {
    return await _repository.getMonthlyStats(
      month: month,
      year: year,
    );
  }
}
