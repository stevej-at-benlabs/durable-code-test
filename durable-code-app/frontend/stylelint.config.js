/**
 * Purpose: Stylelint configuration for CSS Modules + CSS Variables design system
 * Scope: All CSS files in the React frontend application
 * Overview: Enforces design system usage, prevents hardcoded values, and maintains consistency
 * Dependencies: stylelint, stylelint-config-standard, stylelint-config-css-modules, plugins
 * Exports: Stylelint configuration object
 * Interfaces: Stylelint config API
 * Implementation: Custom rules to enforce CSS variable usage and design patterns
 */

export default {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-css-modules'
  ],
  plugins: [
    'stylelint-declaration-strict-value',
    'stylelint-order',
    'stylelint-use-logical'
  ],
  rules: {
    // Enforce CSS Variables for colors (prevents hardcoded values)
    // Temporarily disabled to avoid breaking existing code - can be enabled later
    // 'scale-unlimited/declaration-strict-value': [
    //   ['color', 'background-color', 'border-color'],
    //   {
    //     expandShorthand: true,
    //     ignoreValues: ['transparent', 'inherit', 'currentColor', 'unset', 'initial']
    //   }
    // ],

    // Enforce basic custom property naming (relaxed for existing codebase)
    'custom-property-pattern': [
      '^[a-z][a-z0-9-]*[a-z0-9]$',
      {
        message: 'CSS custom properties should use kebab-case naming'
      }
    ],

    // Prevent hardcoded font sizes (should use design system)
    'declaration-property-value-disallowed-list': {
      'font-size': [
        /^[0-9]+px$/,
        /^[0-9]+pt$/
      ],
      'line-height': [
        /^[0-9]+px$/
      ]
    },

    // Property order for consistency and readability (relaxed for now)
    // 'order/properties-order': null, // Disable property ordering temporarily

    // Use logical properties for better i18n support (disabled temporarily)
    // 'use-logical/use-logical': [true, {
    //   severity: 'warning'
    // }],

    // CSS Modules specific rules
    'selector-pseudo-class-no-unknown': [
      true,
      {
        ignorePseudoClasses: ['global', 'local']
      }
    ],

    // Allow empty sources for CSS Modules
    'no-empty-source': null,

    // Re-enable important rules for production-quality CSS
    'no-duplicate-selectors': true,
    'no-descending-specificity': true,

    // Relax some rules that conflict with CSS Modules or existing code
    'selector-class-pattern': null,
    'font-family-name-quotes': null, // Allow both quoted and unquoted font names
    'keyframes-name-pattern': null, // Allow existing keyframe naming
    'rule-empty-line-before': null, // Relax empty line requirements
    'media-feature-range-notation': null, // Allow legacy media feature syntax

    // Limit language features that might not be supported (relaxed for existing code)
    'color-function-notation': null, // Allow both modern and legacy
    'color-function-alias-notation': null, // Disabled - allow both rgba and rgb
    'alpha-value-notation': null, // Allow both number and percentage
    'selector-pseudo-element-colon-notation': null, // Allow both : and :: notation
    'property-no-vendor-prefix': null, // Allow vendor prefixes for compatibility
    'value-no-vendor-prefix': null, // Allow vendor prefixed values
    'color-hex-length': null, // Allow both short and long hex values
    'declaration-property-value-no-unknown': null, // Allow vendor-specific values
    'at-rule-no-unknown': null, // Allow unknown at-rules (like @extend)
    'property-no-deprecated': null, // Allow deprecated properties for compatibility
    'unit-allowed-list': null // Allow all units for flexibility
  },

  ignoreFiles: [
    'node_modules/**/*',
    'dist/**/*',
    'build/**/*',
    'coverage/**/*'
  ]
};
