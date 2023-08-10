type UserMsgBoxProps = {
  msg: string;
};
export const UserMsgBox: React.FC<UserMsgBoxProps> = ({ msg }) => {
  return (
    <div className="self-end bg-gray-50 rounded-l-lg rounded-br-lg shadow-lg p-4 w-fit bg-green-500/75">
      {msg}
    </div>
  );
};
