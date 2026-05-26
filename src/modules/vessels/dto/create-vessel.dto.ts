import {
  IsString,
  IsNumber,
  Min,
  Max,
  IsOptional,
  IsIn,
} from 'class-validator';
import { ZoneEnum, PropulsionEnum } from '../../shared/entities/vessel.entity';

export class CreateVesselDto {
  @IsString()
  name: string;

  @IsNumber()
  @Min(1)
  @Max(200)
  length: number;

  @IsNumber()
  @Min(1)
  capacity: number;

  @IsOptional()
  @IsIn([ZoneEnum.COASTAL, ZoneEnum.OFFSHORE, ZoneEnum.LIMITED, ZoneEnum.UNLIMITED])
  zone?: ZoneEnum;

  @IsOptional()
  @IsIn([
    PropulsionEnum.DIESEL,
    PropulsionEnum.GASOLINE,
    PropulsionEnum.ELECTRIC,
    PropulsionEnum.HYBRID,
    PropulsionEnum.SAIL,
  ])
  propulsion?: PropulsionEnum;
}