import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";

// const DOMAIN = "http://localhost:3000/api";
const DOMAIN = "http://localhost:60008";

type ResponseChat = {
  text: string;
  blob?: string;
  url?: string;
  id: string;
  tensor?: string;
};
type Response = {
  data: ResponseChat[];
};
type ApiRes = {
  data: Response;
};

type ResData = {
  data: {
    text: string;
  }[];
  parameters: {
    param1: string;
  };
};

type Data = {
  text: string;
  parameters: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const { text, parameters } = req.body as Data;

  const data = {
    data: [
      {
        text: `You: ${text} \nAssistant: `,
      },
    ],
    parameters: {
      param1: parameters,
    },
  } as ResData;

  const axiosRes = await axios.post<ApiRes>(`${DOMAIN}/chat`, data);

  return res.status(200).json(axiosRes.data);
}
