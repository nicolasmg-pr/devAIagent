import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  OneToMany,
} from 'typeorm';
import { Checklist } from '../../checklists/entities/checklist.entity';

export enum VesselType {
  SAILBOAT = 'SAILBOAT',
  MOTORBOAT = 'MOTORBOAT',
   'CATAMARAN',
  YACHT = 'YACHT',
  TRAWLER = 'TRAWLER',
}

@Entity('vessels')
export class Vessel {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'enum', enum: VesselType, length: 10 })
  type: VesselType;

  @Column({ type: 'float' })
  length: number;

  @Column({ type: 'varchar', length: 2 })
  navigation_zone: string;

  @Column({ type: 'integer', name: 'max_passengers' })
  max_passengers: number;

  @Column({ type: 'uuid', name: 'owner_id' })
  owner_id: string;

  @CreateDateColumn({ name: 'created_at', type: 'timestamp' })
  created_at: Date;

  @OneToMany(() => Checklist, (checklist) => checklist.vessel)
  checklists: Checklist[];
}
