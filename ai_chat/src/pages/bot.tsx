import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import { Inter } from "next/font/google";
import Link from "next/link";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { SubmitHandler, useForm } from "react-hook-form";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

const inter = Inter({ subsets: ["latin"] });
const doamin = "http://localhost:3001/api";
const model = ["ChatGLM2-6B", "Llama2-7B", "GPT2"];

const tools = [
  {
    name: "faceswapgan",
    description: "Use faceswwpgan to swap faces",
  },
];

const FormSchema = z.object({
  model: z.enum(["ChatGLM2-6B", "Llama2-7B", "GPT2"], {
    required_error: "You need to select a model",
  }),
  tool: z.enum(["faceswapgan"], {
    required_error: "You need to select a Tool",
  }),
  filePath: z.string(),
});

export default function Bot() {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  //@todo: drag and drop file here
  // const onDrop = useCallback((acceptedFiles: File[]) => {
  //   // Do something with the files
  // }, []);
  // const { getRootProps, getInputProps, isDragActive, acceptedFiles } =
  //   useDropzone({ onDrop });
  // const files = acceptedFiles.map((file) => (
  //   <span key={file.name}>
  //     {file.name}
  //     <br />
  //   </span>
  // ));

  const onSubmit: SubmitHandler<z.infer<typeof FormSchema>> = async (data) => {
    console.log(data);
    const { model, tool, filePath } = data;

    // application/pdf
  };

  const fetchChat = async () => {
    try {
      const apiRes = await axios
        .post(`${doamin}/createYaml`, {
          // text: msg,
          parameters: "hello world",
        })
        .then((response) => {
          const { data } = response as ApiRes;
          console.log("success");
          // const { data: chatRes } = data;
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
    <div className="flex h-full w-full flex-col items-center justify-center">
      <button onClick={fetchChat} className="text-white">
        click
      </button>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit((data) => void onSubmit(data))}
          className="flex w-full flex-col space-y-6 rounded-md bg-gray-600/20 p-10 shadow-md "
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
            render={() => (
              <FormItem>
                <div className="mb-4">
                  <FormLabel className="text-base">Tools</FormLabel>
                </div>
                {tools.map((item) => (
                  <FormField
                    key={item.name}
                    control={form.control}
                    name="tool"
                    render={({ field }) => {
                      return (
                        <FormItem
                          key={item.name}
                          className="flex flex-row items-start space-x-3 space-y-0"
                        >
                          <FormControl>
                            <Checkbox
                              checked={field.value?.includes(item.name)}
                              // onCheckedChange={(checked) => {
                              //   return checked
                              //     ? field.onChange([
                              //         ...field.value,
                              //         item.name,
                              //       ])
                              //     : field.onChange(
                              //         field.value?.filter(
                              //           (value) => value !== item.id,
                              //         ),
                              //       );
                              // }}
                            />
                          </FormControl>
                          <FormLabel className="font-normal">
                            {item.name}
                          </FormLabel>
                        </FormItem>
                      );
                    }}
                  />
                ))}
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="filePath"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Username</FormLabel>
                <FormControl>
                  <Input placeholder="Path" {...field} />
                </FormControl>

                <FormMessage />
              </FormItem>
            )}
          />

          {/* <div className="grid w-full max-w-sm items-center gap-1.5">
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
            </div> */}
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
          <Button variant={"outline"} asChild className="self-center">
            <a download href={"/bot.yaml"}>
              Download Bot
            </a>
          </Button>
          {/* <Button type="submit">Download bot file</Button> */}
        </form>
      </Form>
    </div>
  );
}
