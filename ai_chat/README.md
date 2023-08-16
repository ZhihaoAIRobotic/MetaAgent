## Getting Started

1. install `yarn` [https://classic.yarnpkg.com/lang/en/docs/install/#mac-stable]
2. In this dictionary, run `yarn` in the terminal to install all dependency
3. start the development server: `yarn dev`

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Update HTTP request domain :

The `pages/api` directory is mapped to `/api/*`. Files in this directory are treated as [API routes](https://nextjs.org/docs/api-routes/introduction) instead of React pages.

Go to : `src/pages/api/chat.ts:6 ` replace `DEMAIN` to new path

For example, if the jian executor is 0.0.0.0:60008, DEMAIN will be "http://localhost:60008"