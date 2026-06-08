module.exports = {
  apps: [{
    name: 'virel',
    script: 'python',
    args: '-m virel.core',
    cwd: '/root/virel',
    instances: 1,
    autorestart: true,
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};