package level2;
import java.util.*;
public class largestnumber {
   public static void main(String[]args){
    Scanner sc = new Scanner(System.in);
    int num1, num2, num3;
    System.out.println("enter Three number to find largest amaong them");
         System.out.print("enetr your first number:");
             num1=sc.nextInt();
        System.out.print("enter you second number:");
            num2=sc.nextInt();
        System.out.print("enter your third number");
            num3=sc.nextInt();
       if (num1>=num2&&num1>=num3) {
        System.out.println("first number is largest number");
       }
       else if(num2>=num1&&num2>=num3){
        System.out.println("second number is largest number");
       }
       else{
        System.out.println("third number is the largest number");
       }
    sc.close();
   }

}
