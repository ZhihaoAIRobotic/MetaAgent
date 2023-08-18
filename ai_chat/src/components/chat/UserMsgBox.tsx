type UserMsgBoxProps = {
  msg: string;
};
export const UserMsgBox: React.FC<UserMsgBoxProps> = ({ msg }) => {
  return (
    <div className="w-fit self-end rounded-l-lg rounded-br-lg bg-gray-50 bg-green-500/75 p-4 shadow-lg">
      {msg}
    </div>
  );
};
