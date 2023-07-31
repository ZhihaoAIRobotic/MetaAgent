// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";

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
// temp data
// const doamin = "http://localhost:3000/api";
// const doamin = "http://region-46.seetacloud.com:27604";
const doamin = "http://region-3.seetacloud.com:57942";
// curl --request POST 'http://region-46.seetacloud.com:27604/chat' --header 'Content-Type: application/json' -d '{"data": [{"text": "hallo,who are you"}], "parameters": {"param1": "hello world"}}'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const { text, parameters } = req.body as Data;

  const data = {
    data: [
      {
        text,
      },
    ],
    parameters: {
      param1: parameters,
    },
  } as ResData;

  const axiosRes = await axios.post<ApiRes>(`${doamin}/chat`, data);

  console.log(axiosRes.data);
  return res.status(200).json(axiosRes.data);
}
