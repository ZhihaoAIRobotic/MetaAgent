import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import Link from "next/link";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { SubmitHandler, useForm } from "react-hook-form";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { BotIcon } from "@/images/Bot";
import { Chat } from "@/images/Chat";

type ResponseChat = {
  text: string;
};
type Response = {
  data: ResponseChat[];
};
type ApiRes = {
  data: Response;
};

const doamin = "http://localhost:3000/api";
const model = ["ChatGML2-6B"];

const tools = [
  {
    name: "faceswapgan",
    description: "Use faceswwpgan to swap faces",
  },
];

const FormSchema = z.object({
  model: z.enum(["ChatGML2-6B"], {
    required_error: "You need to select a model",
  }),
  tool: z.enum(["faceswapgan"], {
    required_error: "You need to select a Tool",
  }),
});

export default function Bot() {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Do something with the files
  }, []);
  const { getRootProps, getInputProps, isDragActive, acceptedFiles } =
    useDropzone({ onDrop });
  const files = acceptedFiles.map((file) => (
    <span key={file.name}>
      {file.name}
      <br />
    </span>
  ));

  const onSubmit: SubmitHandler<z.infer<typeof FormSchema>> = async (data) => {
    console.log(data);

    // application/pdf
  };

  const fetchChat = async (msg: string) => {
    try {
      const apiRes = await axios
        .post(`${doamin}/createYaml`, {
          text: msg,
          parameters: "hello world",
        })
        .then((response) => {
          const { data } = response as ApiRes;
          console.log("success");
          const { data: chatRes } = data;
          // const { text, blob } = chatRes[0];
          // const newChat = {
          //   message: text,
          //   blob,
          //   createAt: Date.now(),
          //   senderId: 1,
          // };
          // return newChat;
        })
        .catch((err) => {
          // console.log("error: ", err);
        });
      return apiRes;
    } catch (err) {
      // console.log(err);
    }
  };

  // const onFileUpload = (event:) => {
  //   // const file = document.getElementById("picture") as HTMLInputElement;

  //   console.log(event);
  // };

  return (
    <div className="bg-gray-900">
      <div className="fixed left-10 top-4 flex h-fit flex-col gap-4 rounded-full bg-gray-100/80 p-2">
        <Link href={"/"} className="rounded-full p-2 hover:bg-gray-500/50">
          <Chat />
        </Link>
        <Link href={"/bot"} className="rounded-full p-2 hover:bg-gray-500/50">
          <BotIcon />
        </Link>
      </div>
      <main
        className={`flex min-h-screen flex-col items-center justify-between p-12`}
      >
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((data) => void onSubmit(data))}
            className="w-full max-w-xl space-y-6 rounded-md bg-gray-800/50 p-10 shadow-md"
          >
            <FormField
              control={form.control}
              name="model"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Model</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a Model" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {model.map((item) => (
                        <SelectItem key={item} value={item}>
                          {item}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="tool"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel className="font-semibold">Tools</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="flex flex-col space-y-1"
                    >
                      {tools.map((item) => (
                        <FormItem
                          className="flex items-center space-x-3 space-y-0"
                          key={item.name}
                        >
                          <FormControl>
                            <RadioGroupItem value={item.name} />
                          </FormControl>
                          <FormLabel className="font-normal">
                            {item.name}
                          </FormLabel>
                        </FormItem>
                      ))}
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="file" className="font-semibold">
                File
              </Label>
              <div
                {...getRootProps()}
                className="flex h-40 w-full flex-col items-center justify-center rounded-md border border-gray-400"
              >
                <input {...getInputProps()} />

                {files.length > 0 ? (
                  <div className="text-gray-50">{files}</div>
                ) : isDragActive ? (
                  <p className="text-gray-50">Drop the file here ...</p>
                ) : (
                  <p className="text-gray-50">
                    Drag & drop files here, or click to select file
                  </p>
                )}
              </div>
            </div>
            {/* <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="file" className="font-semibold">
                File
              </Label>
              <Input
                id="file"
                type="file"
                accept=".pdf"
                onChange={onFileUpload}
                className="w-full bg-gray-800/50 text-gray-50"
              />
            </div> */}
            <Separator />
            <Button variant={"secondary"} asChild>
              <a download href={"/bot.yaml"}>
                Download Bot
              </a>
            </Button>
            {/* <Button type="submit">Download bot file</Button> */}
          </form>
        </Form>
      </main>
    </div>
  );
}
