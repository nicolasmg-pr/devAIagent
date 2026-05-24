import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Category } from './category.entity';
import { CreateCategoryDto } from './dto/create-category.dto';
import { UpdateCategoryDto } from './dto/update-category.dto';

@Injectable()
export class CategoryService {
  constructor(
    @InjectRepository(Category)
    private categoriesRepo: Repository<Category>,
  ) {}

  async create(dto: CreateCategoryDto, userId: string) {
    const category = this.categoriesRepo.create({ ...dto, user_id: userId });
    return this.categoriesRepo.save(category);
  }

  async findAll(userId: string) {
    return this.categoriesRepo.find({ where: { user_id: userId } });
  }

  async findOne(id: string, userId: string) {
    const category = await this.categoriesRepo.findOne({ where: { id, user_id: userId } });
    if (!category) throw new NotFoundException('Categoría no encontrada');
    return category;
  }

  async update(id: string, dto: UpdateCategoryDto, userId: string) {
    const category = await this.findOne(id, userId);
    Object.assign(category, dto);
    return this.categoriesRepo.save(category);
  }

  async remove(id: string, userId: string) {
    const category = await this.findOne(id, userId);
    return this.categoriesRepo.remove(category);
  }
}