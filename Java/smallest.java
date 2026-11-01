 import java.util.*;
 public class smallest {
  public static void main(String[]args){
    Scanner sc = new Scanner(System.in);
    int num1, num2, num3;
    System.out.print("enetr your first number:");
    num1=sc.nextInt();
    System.out.print("enter you second number:");
    num2=sc.nextInt();
    System.out.print("enter your third number:");
    num3= sc.nextInt();
    if (num1<=num2&& num1<=num3){
        System.out.println("smallest number is :" +num1);
    }
 else if(num2<=num1&& num2<=num3){
    System.out.println(" smallest number is: " +num2);
        }
        else{
            System.out.println("the smallest number is: " +num3);      
    }
    sc.close();
  }

}
