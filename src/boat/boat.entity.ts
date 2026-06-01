import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BoatModule } from './boat/boat.module';
import { ChecklistModule } from './checklist/checklist.module';
import { ZoneModule } from './zone/zone.module';
import { WeatherModule } from './weather/weather.module';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT) || 5432,
      username: process.env.DB_USERNAME || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres',
      database: process.env.DB_NAME || 'presailing',
      autoLoadEntities: true,
      synchronize: true,
    }),
    BoatModule,
    ChecklistModule,
    ZoneModule,
    WeatherModule,
  ],
})
export class AppModule {}