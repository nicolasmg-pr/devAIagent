import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Protocol } from '../../shared/entities/protocol.entity';
import { ProtocolsController } from './protocols.controller';
import { ProtocolsService } from './protocols.service';

@Module({
  imports: [TypeOrmModule.forFeature([Protocol])],
  controllers: [ProtocolsController],
  providers: [ProtocolsService],
  exports: [ProtocolsService],
})
export class ProtocolsModule {}