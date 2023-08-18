type BotMsgBoxProps = {
  msg: string;
};
export const BotMsgBox: React.FC<BotMsgBoxProps> = ({ msg }) => {
  return (
    <div className="w-fit self-start rounded-r-lg rounded-bl-lg bg-gray-50 p-4 shadow-lg">
      {msg}
    </div>
  );
};
