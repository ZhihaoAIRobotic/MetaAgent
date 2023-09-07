import type { NextApiRequest, NextApiResponse } from "next";
import writeYamlFile from "write-yaml-file";

type Data = {
  text: string;
  parameters: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const { text, parameters } = req.body as Data;
  writeYamlFile("./bot.yaml", { foo: true })
    .then(() => {
      console.log("done");
    })
    .catch((err) => {
      console.log(err);
    });

  const data = {};

  return res.status(200).json(data);
}

// LLM_Model: ChatGML2-6B
// PDF_path: ./data_cache/PDF_path
// Tools:
//   -name: "faceswapgan"
//   -description: "use faceswapgan to swap faces"
