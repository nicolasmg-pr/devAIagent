import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Vessel } from './entities/vessel.entity';
import { VesselsService } from './vessels.service';
import { VesselsController } from './vessels.controller';

@Module({
  imports: [TypeOrmModule.forFeature([Vessel])],
  controllers: [VesselsController],
  providers: [VesselsService],
  exports: [VesselsService],
})
export class VesselsModule {}
