import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne } from 'typeorm';
import { User } from '../users/user.entity';
import { Category } from '../categories/category.entity';

@Entity('budgets')
export class Budget {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ name: 'monthly_limit', type: 'decimal', precision: 10, scale: 2 })
  monthly_limit: number;

  @Column({ name: 'alert_threshold', default: 80 })
  alert_threshold: number;

  @ManyToOne(() => Category, { nullable: true })
  category: Category;

  @Column({ name: 'category_id', nullable: true })
  category_id: string;

  @ManyToOne(() => User, (user) => user.budgets)
  user: User;

  @Column({ name: 'user_id' })
  user_id: string;

  @CreateDateColumn({ name: 'created_at' })
  created_at: Date;
}