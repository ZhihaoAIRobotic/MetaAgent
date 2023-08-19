import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BotIcon } from "@/images/Bot";
import { Chat } from "@/images/Chat";

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

  function onSubmit(data: z.infer<typeof FormSchema>) {
    // console.log(data);
  }

  const onFileUpload = ({ target }: { target: HTMLInputElement }) => {
    // const file = document.getElementById("picture") as HTMLInputElement;
    console.log(target.value);
  };

  return (
    <div>
      <div className="fixed left-10 top-4 flex h-fit flex-col gap-4 rounded-md bg-gray-200/50 p-2">
        <Link href={"/"} className="rounded p-2 hover:bg-gray-500/50">
          <Chat />
        </Link>
        <Link href={"/bot"} className="rounded p-2 hover:bg-gray-500/50">
          <BotIcon />
        </Link>
      </div>
      <main
        className={`flex min-h-screen flex-col items-center justify-between p-12`}
      >
        <Form {...form}>
          <form
            onSubmit={void form.handleSubmit(onSubmit)}
            className="w-full max-w-xl space-y-6 rounded-md border border-gray-700 p-10  shadow-md "
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
              <Input
                id="file"
                type="file"
                accept=".pdf"
                onChange={onFileUpload}
              />
            </div>
            <Button type="submit">Submit</Button>
          </form>
        </Form>
      </main>
    </div>
  );
}
