import java.util.*;
public class rectangle {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int length, breadth, area, perimeter;

        System.out.print("enter you length:");
        length = sc.nextInt();
         System.out.print("enter you breadth:");
    breadth = sc.nextInt();

      area = breadth * length;
      perimeter = 2 * (length + breadth);

      System.out.println("your rectangle area is:"+ area);
      System.out.println("your rectangle perimeter is : "+ perimeter);

     sc.close();
  }
}