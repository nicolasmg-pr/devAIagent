import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { HealthModule } from './common/health/health.module';
import { AuthModule } from './modules/auth/auth.module';
import { VesselsModule } from './modules/vessels/vessels.module';
import { ChecklistsModule } from './modules/checklists/checklists.module';
import { ProtocolsModule } from './modules/protocols/protocols.module';
import { SyncModule } from './modules/sync/sync.module';
import { User } from './shared/entities/user.entity';
import { Vessel } from './shared/entities/vessel.entity';
import { Protocol } from './shared/entities/protocol.entity';
import { ChecklistInstance } from './shared/entities/checklist-instance.entity';
import { ChecklistItem } from './shared/entities/checklist-item.entity';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get('DB_HOST', 'localhost'),
        port: configService.get('DB_PORT', 5432),
        username: configService.get('DB_USERNAME', 'postgres'),
        password: configService.get('DB_PASSWORD', 'postgres'),
        database: configService.get('DB_NAME', 'marinecheck_pro'),
        entities: [User, Vessel, Protocol, ChecklistInstance, ChecklistItem],
        synchronize: configService.get('NODE_ENV') !== 'production',
        logging: configService.get('NODE_ENV') !== 'production',
      }),
    }),
    HealthModule,
    AuthModule,
    VesselsModule,
    ChecklistsModule,
    ProtocolsModule,
    SyncModule,
  ],
})
export class AppModule {}