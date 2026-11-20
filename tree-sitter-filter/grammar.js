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
    comparison: $ => seq($.identifier, "=", $.string),
    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_.]*/,
    string: $ => /"[^"]*"/,
  }
});
