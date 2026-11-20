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

  rules: {
    query: $ => $.comparison,
    comparison: $ => seq(
      $.identifier,
      choice("=", "!=", ">", "<", ">=", "<="),
      $._value,
    ),
    _value: $ => choice($.string, $.number),
    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    string: $ => /"[^"]*"/,
    number: $ => /\d+(\.\d+)?/,
  }
});
