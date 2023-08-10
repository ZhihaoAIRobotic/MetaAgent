type BotMsgBoxProps = {
  msg: string;
};
export const BotMsgBox: React.FC<BotMsgBoxProps> = ({ msg }) => {
  return (
    <div className="self-start bg-gray-50 rounded-r-lg rounded-bl-lg shadow-lg p-4 w-fit">
      {msg}
    </div>
  );
};
