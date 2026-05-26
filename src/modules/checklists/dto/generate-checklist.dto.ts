import { IsUUID, IsString, IsNotEmpty } from 'class-validator';

export class GenerateChecklistDto {
  @IsUUID()
  @IsNotEmpty()
  vessel_id: string;

  @IsString()
  @IsNotEmpty()
  protocol_version: string;
}