# CSS Factor Tool Guide

This tool provides three options for processing your CSS:

## 1. Factor

The "factor" option optimizes your CSS by grouping similar rules and combining selectors with identical declarations.

Example:
```css
/* Input */
h1 { color: blue; }
.header { font-size: 20px; }
h2 { color: blue; }

/* Output */
h1, h2 { color: blue; }
.header { font-size: 20px; }
```

This makes your CSS more compact and easier to maintain by reducing redundancy.

## 2. Explode

The "explode" option breaks down CSS rules into the most granular form possible, with each selector-property pair becoming its own rule.

Example:
```css
/* Input */
h1, h2 { color: blue; font-size: 20px; }

/* Output */
h1 { color: blue; }
h1 { font-size: 20px; }
h2 { color: blue; }
h2 { font-size: 20px; }
```

This is useful for analyzing the full impact of your CSS or as a preprocessing step.

## 3. Identity

The "identity" option processes the CSS without changing its structure, but standardizes its format.

Example:
```css
/* Input */
h1{color:blue;} .header{font-size:20px;}

/* Output */
h1 { color: blue; }
.header { font-size: 20px; }
```

This is useful for validating CSS, standardizing formatting, or as a "no-op" option.
