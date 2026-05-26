import {
  Controller,
  Post,
  Body,
  UsePipes,
  ValidationPipe,
} from '@nestjs/common';
import { SyncService } from './sync.service';
import { SyncChangesDto } from './dto/sync-changes.dto';

@Controller('sync')
export class SyncController {
  constructor(private readonly syncService: SyncService) {}

  @Post('state')
  @UsePipes(new ValidationPipe({ whitelist: true, transform: true }))
  async syncState(@Body() syncDto: SyncChangesDto) {
    return this.syncService.processSync(syncDto);
  }
}