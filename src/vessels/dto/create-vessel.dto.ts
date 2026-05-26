import {
  IsString,
  IsNumber,
  IsInt,
  IsUUID,
  IsEnum,
  Min,
  Max,
} from 'class-validator';
import { VesselType } from '../entities/vessel.entity';

export class CreateVesselDto {
  @IsEnum(VesselType, {
    message: 'Type must be one of: SAILBOAT, MOTORBOAT, CATAMARAN, YACHT, TRAWLER',
  })
  type: VesselType;

  @IsNumber({}, { message: 'Length must be a number' })
  @Min(1, { message: 'Length must be at least 1 meter' })
  @Max(200, { message: 'Length cannot exceed 200 meters' })
  length: number;

  @IsString()
  navigation_zone: string;

  @IsInt()
  @Min(0, { message: 'Max passengers cannot be negative' })
  @Max(1000, { message: 'Max passengers cannot exceed 1000' })
  max_passengers: number;

  @IsUUID('4', { message: 'Owner ID must be a valid UUID' })
  owner_id: string;
}
