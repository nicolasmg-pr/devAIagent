import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mocktail/mocktail.dart';
import 'package:expense_tracker/providers/expense_provider.dart';
import 'package:expense_tracker/views/add_expense_view.dart';
import 'package:expense_tracker/models/expense.dart';

class MockExpenseProvider extends Mock implements ExpenseProvider {}

void main() {
  late MockExpenseProvider mockExpenseProvider;

  setUp(() => mockExpenseProvider = MockExpenseProvider());

  testWidgets('AddExpenseView renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<ExpenseProvider>(
          create: (_) => mockExpenseProvider,
          child: const AddExpenseView(),
        ),
      ),
    );

    expect(find.text('Add Expense'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(3));
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('AddExpenseView submits form', (WidgetTester tester) async {
    when(() => mockExpenseProvider.addExpense(any())).thenAnswer((_) async {});

    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<ExpenseProvider>(
          create: (_) => mockExpenseProvider,
          child: const AddExpenseView(),
        ),
      ),
    );

    await tester.enterText(find.byType(TextFormField).at(0), '100');
    await tester.enterText(find.byType(TextFormField).at(1), '2023-10-01');
    await tester.enterText(find.byType(TextFormField).at(2), 'Test');
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    verify(() => mockExpenseProvider.addExpense(any())).called(1);
  });

  testWidgets('AddExpenseView shows error on empty fields', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider<ExpenseProvider>(
          create: (_) => mockExpenseProvider,
          child: const AddExpenseView(),
        ),
      ),
    );

    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    expect(find.text('Please fill all fields'), findsOneWidget);
  });
}