import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, OneToMany } from 'typeorm';
import { User } from '../users/user.entity';
import { Expense } from '../expenses/expense.entity';

@Entity('categories')
export class Category {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ length: 50 })
  name: string;

  @Column({ length: 7, nullable: true })
  color: string;

  @Column({ name: 'is_default', default: false })
  is_default: boolean;

  @ManyToOne(() => User, (user) => user.expenses)
  user: User;

  @Column({ name: 'user_id' })
  user_id: string;

  @OneToMany(() => Expense, (expense) => expense.category)
  expenses: Expense[];

  @CreateDateColumn({ name: 'created_at' })
  created_at: Date;
}