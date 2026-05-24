import 'package:dartz/dartz.dart';
import '../../../core/errors/failures.dart';
import '../entities/stat_entities.dart';

abstract class StatsRepository {
  Future<Either<Failure, StatsResponse>> getMonthlyStats({
    int? month,
    int? year,
  });
}
