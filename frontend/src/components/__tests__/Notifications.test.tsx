import { render } from "@testing-library/react";
import Notifications from "@/components/Notifications";

test("renders notification component snapshot", () => {
  const { container } = render(<Notifications />);
  expect(container).toMatchSnapshot();
});
