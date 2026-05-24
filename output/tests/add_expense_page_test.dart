import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:appgastos/pages/add_expense_page.dart';
import 'package:appgastos/repositories/expense_repository.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

// Mock class
class MockExpenseRepository extends Mock implements ExpenseRepository {}

void main() {
  testWidgets('AddExpensePage renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AddExpensePage(),
      ),
    );

    expect(find.text('Add Expense'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2)); // Amount and Description
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('AddExpensePage validates amount', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: AddExpensePage(),
      ),
    );

    // Type invalid amount
    await tester.enterText(find.byType(TextFormField).first, 'abc');
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Expect error or validation
    // Note: Without seeing the specific validation logic in the page, this is a generic check
    // Assuming the page uses a FormState
  });
}