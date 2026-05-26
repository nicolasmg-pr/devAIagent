import { Injectable, Logger, BadRequestException } from '@nestjs/common';
import { SyncChangesDto } from './dto/sync-changes.dto';

interface SyncResult {
  sync_status: 'success' | 'conflict';
  resolved_items: number;
  conflicts?: Array<{
    entity_type: string;
    entity_id: string;
    server_value: any;
    client_value: any;
  }>;
}

@Injectable()
export class SyncService {
  private readonly logger = new Logger(SyncService.name);

  async processSync(
    syncDto: SyncChangesDto,
  ): Promise<SyncResult> {
    const { local_timestamp, changes } = syncDto;

    if (!changes || changes.length === 0) {
      return {
        sync_status: 'success',
        resolved_items: 0,
      };
    }

    let resolvedItems = 0;
    const conflicts: SyncResult['conflicts'] = [];

    for (const change of changes) {
      try {
        const result = await this.applyChange(change, local_timestamp);
        if (result.hasConflict) {
          conflicts.push({
            entity_type: change.entity_type,
            entity_id: change.entity_id,
            server_value: result.serverValue,
            client_value: change.data,
          });
        } else {
          resolvedItems++;
        }
      } catch (error) {
        this.logger.error(
          `Error applying change for ${change.entity_type} ${change.entity_id}: ${error.message}`,
        );
        conflicts.push({
          entity_type: change.entity_type,
          entity_id: change.entity_id,
          server_value: null,
          client_value: change.data,
        });
      }
    }

    const syncStatus =
      conflicts.length > 0 ? 'conflict' : 'success';

    return {
      sync_status: syncStatus,
      resolved_items: resolvedItems,
      ...(conflicts.length > 0 && { conflicts }),
    };
  }

  private async applyChange(
    change: {
      entity_type: string;
      entity_id: string;
      action?: string;
      data?: Record<string, any>;
      local_timestamp: number;
    },
    localTimestamp: number,
  ): Promise<{
    hasConflict: boolean;
    serverValue?: any;
  }> {
    switch (change.entity_type) {
      case 'vessel':
        return this.applyVesselChange(change);
      case 'checklist_instance':
        return this.applyChecklistChange(change);
      case 'checklist_item':
        return this.applyItemChange(change);
      default:
        return { hasConflict: false };
    }
  }

  private async applyVesselChange(
    change: any,
  ): Promise<{ hasConflict: boolean; serverValue?: any }> {
    const { action, data } = change;

    if (action === 'delete') {
      return { hasConflict: false };
    }

    if (action === 'create' || action === 'update') {
      return {
        hasConflict: false,
        serverValue: data,
      };
    }

    return { hasConflict: false };
  }

  private async applyChecklistChange(
    change: any,
  ): Promise<{ hasConflict: boolean; serverValue?: any }> {
    const { action, data } = change;

    if (action === 'delete') {
      return { hasConflict: false };
    }

    if (action === 'create' || action === 'update') {
      return {
        hasConflict: false,
        serverValue: data,
      };
    }

    return { hasConflict: false };
  }

  private async applyItemChange(
    change: any,
  ): Promise<{ hasConflict: boolean; serverValue?: any }> {
    const { action, data } = change;

    if (action === 'delete') {
      return { hasConflict: false };
    }

    if (action === 'create' || action === 'update') {
      return {
        hasConflict: false,
        serverValue: data,
      };
    }

    return { hasConflict: false };
  }

  async getSyncState(
    userId: string,
    sinceTimestamp?: number,
  ): Promise<{
    last_sync: string;
    pending_changes: number;
    server_timestamp: number;
  }> {
    return {
      last_sync: new Date().toISOString(),
      pending_changes: 0,
      server_timestamp: Date.now(),
    };
  }
}