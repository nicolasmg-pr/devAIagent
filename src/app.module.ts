import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { VesselsModule } from './vessels/vessels.module';
import { ChecklistsModule } from './checklists/checklists.module';
import { RulesModule } from './rules/rules.module';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT) || 5432,
      username: process.env.DB_USERNAME || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres',
      database: process.env.DB_NAME || 'maritime_checklist',
      autoLoadEntities: true,
      synchronize: process.env.NODE_ENV !== 'production',
    }),
    VesselsModule,
    ChecklistsModule,
    RulesModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
