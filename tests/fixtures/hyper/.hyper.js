// Hyper configuration file for testing

module.exports = {
  config: {
    // Update channel
    updateChannel: 'stable',

    // Font settings
    fontSize: 14,
    fontFamily: 'JetBrains Mono, Menlo, "DejaVu Sans Mono", monospace',
    fontWeight: 'normal',
    fontWeightBold: 'bold',
    lineHeight: 1.2,
    letterSpacing: 0,

    // Cursor settings
    cursorColor: 'rgba(248,28,229,0.8)',
    cursorAccentColor: '#000',
    cursorShape: 'BLOCK',
    cursorBlink: true,

    // Colors
    foregroundColor: '#c5c8c6',
    backgroundColor: '#1d1f21',
    selectionColor: 'rgba(248,28,229,0.3)',
    borderColor: '#333',

    // ANSI color palette
    colors: {
      black: '#282a2e',
      red: '#a54242',
      green: '#8c9440',
      yellow: '#de935f',
      blue: '#5f819d',
      magenta: '#85678f',
      cyan: '#5e8d87',
      white: '#707880',
      lightBlack: '#373b41',
      lightRed: '#cc6666',
      lightGreen: '#b5bd68',
      lightYellow: '#f0c674',
      lightBlue: '#81a2be',
      lightMagenta: '#b294bb',
      lightCyan: '#8abeb7',
      lightWhite: '#c5c8c6'
    },

    // Shell settings
    shell: '/bin/zsh',
    shellArgs: ['--login'],

    // Environment variables
    env: {
      TERM: 'xterm-256color'
    },

    // Window settings
    padding: '12px 14px',
    scrollback: 10000,

    // Behavior settings
    copyOnSelect: false,

    // Hyper-specific settings
    webGLRenderer: true
  },

  // Plugin list
  plugins: [
    'hyper-snazzy',
    'hyper-tabs-enhanced'
  ],

  // Local plugins
  localPlugins: [],

  // Custom keymaps
  keymaps: {
    'window:devtools': 'cmd+alt+o',
    'tab:new': 'cmd+t',
    'pane:splitVertical': 'cmd+d'
  }
};
