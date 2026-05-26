import { Injectable } from '@nestjs/common';
import { InjectConnection } from '@nestjs/typeorm';
import { Connection } from 'typeorm';

@Injectable()
export class HealthService {
  constructor(@InjectConnection() private readonly connection: Connection) {}

  async getHealthStatus(): Promise<{
    status: string;
    uptime: number;
    db_status: string;
    timestamp: string;
  }> {
    let dbStatus = 'disconnected';

    try {
      if (this.connection.isInitialized) {
        await this.connection.query('SELECT 1');
        dbStatus = 'connected';
      }
    } catch (error) {
      dbStatus = 'error';
    }

    const isHealthy = dbStatus === 'connected';

    return {
      status: isHealthy ? 'healthy' : 'unhealthy',
      uptime: process.uptime(),
      db_status: dbStatus,
      timestamp: new Date().toISOString(),
    };
  }
}