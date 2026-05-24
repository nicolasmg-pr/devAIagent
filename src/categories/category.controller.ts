import { Controller, Get, Post, Put, Delete, Body, Param, UseGuards } from '@nestjs/common';
import { CategoryService } from './category.service';
import { CreateCategoryDto } from './dto/create-category.dto';
import { UpdateCategoryDto } from './dto/update-category.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@Controller('api/v1/categories')
@UseGuards(JwtAuthGuard)
export class CategoryController {
  constructor(private categoryService: CategoryService) {}

  @Post()
  async create(@Body() dto: CreateCategoryDto, @CurrentUser() userId: string) {
    return this.categoryService.create(dto, userId);
  }

  @Get()
  async findAll(@CurrentUser() userId: string) {
    const categories = await this.categoryService.findAll(userId);
    return { data: categories.map((cat) => ({ id: cat.id, name: cat.name, color: cat.color, isDefault: cat.is_default })) };
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() dto: UpdateCategoryDto, @CurrentUser() userId: string) {
    await this.categoryService.update(id, dto, userId);
    return { id, status: 'updated' };
  }

  @Delete(':id')
  async remove(@Param('id') id: string, @CurrentUser() userId: string) {
    await this.categoryService.remove(id, userId);
    return { status: 'deleted' };
  }
}