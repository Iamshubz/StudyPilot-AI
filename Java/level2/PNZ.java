package level2;
import java.util.*;
public class PNZ {
    public static void main(String[]args){
        Scanner sc = new Scanner(System.in);
        int num;
        System.out.print("enter your number:");
        num = sc.nextInt();
        if(num>0){
            System.out.println("Number is Positive");
        } else if (num<0){
            System.out.println("number is negative");  
        }
        else{
            System.out.println("give number is zero");
        }
        sc.close();
    }
}
