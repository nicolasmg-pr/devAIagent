import {
  IsNumber,
  IsArray,
  IsString,
  ValidateNested,
  IsOptional,
} from 'class-validator';
import { Type } from 'class-transformer';

class ChangeEntry {
  @IsString()
  entity_type: string;

  @IsString()
  entity_id: string;

  @IsOptional()
  @IsString()
  action?: 'create' | 'update' | 'delete';

  @IsOptional()
  data?: Record<string, any>;

  @IsNumber()
  local_timestamp: number;
}

export class SyncChangesDto {
  @IsNumber()
  local_timestamp: number;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => ChangeEntry)
  changes: ChangeEntry[];
}