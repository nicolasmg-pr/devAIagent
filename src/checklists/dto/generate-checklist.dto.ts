import { IsUUID, IsNumber, IsOptional, IsString } from 'class-validator';

export class GenerateChecklistDto {
  @IsUUID('4', { message: 'Vessel ID must be a valid UUID' })
  vessel_id: string;

  @IsNumber({}, { message: 'Passenger count must be a number' })
  @IsOptional()
  passenger_count?: number;

  @IsString()
  @IsOptional()
  weather_conditions?: string;
}
