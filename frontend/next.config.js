/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // In local dev, proxy /api/* to the FastAPI backend on port 8000
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:8000/api/:path*',
        },
      ]
    }
    return []
  },
}

module.exports = nextConfig
