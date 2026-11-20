/**
 * @file DSL filter grammar
 * @author Muhammad Salman Al Farisi
 * @license MIT
 */

/// <reference types="tree-sitter-cli/dsl" />
// @ts-check

export default grammar({
  name: "filter",
  extras: $ => [/\s/],
  word: $ => $.identifier,

  rules: {
    query: $ => $._expr,
    _expr: $ => choice($.comparison, $.and_expression, $.or_expression),
    comparison: $ => seq(
      $.identifier,
      choice("=", "!=", ">", "<", ">=", "<="),
      $._value,
    ),
    or_expression: $ => prec.left(1, seq($._expr, "or", $._expr)),
    and_expression: $ => prec.left(2, seq($._expr, "and", $._expr)),
    _value: $ => choice($.string, $.number),
    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    string: $ => /"[^"]*"/,
    number: $ => /\d+(\.\d+)?/,
  }
});
