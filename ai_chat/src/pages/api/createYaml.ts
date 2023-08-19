// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";
import writeYamlFile from "write-yaml-file";

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
  console.log("catch");

  const { text, parameters } = req.body as Data;
  writeYamlFile("/bot.yaml", { foo: true })
    .then(() => {
      console.log("done");
    })
    .catch((err) => {
      console.log(err);
    });
  // const data = {
  //   data: [
  //     {
  //       text: `You: ${text} \nAssistant: `,
  //     },
  //   ],
  //   parameters: {
  //     param1: parameters,
  //   },
  // } as ResData;

  // const axiosRes = await axios.post<ApiRes>(`${DOMAIN}/chat`, data);

  // console.log(axiosRes.data);

  return res.status(200).json("axiosRes.data");
}
