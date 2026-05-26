import {
  IsString,
  IsDate,
  IsBoolean,
  IsOptional,
  IsObject,
} from 'class-validator';
import { Type } from 'class-transformer';

export class CreateProtocolDto {
  @IsString()
  version: string;

  @IsDate()
  @Type(() => Date)
  effective_date: Date;

  @IsObject()
  @IsOptional()
  rules_payload?: Record<string, any>;

  @IsBoolean()
  @IsOptional()
  is_active?: boolean;
}