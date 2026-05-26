import { IsUUID, IsNotEmpty } from 'class-validator';

export class GetProtocolSyncDto {
  @IsUUID()
  @IsNotEmpty()
  vessel_id: string;
}