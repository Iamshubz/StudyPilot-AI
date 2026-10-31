package level1;
import java.util.*;
public class timeconversion {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int totalseconds,hours,minutes,seconds,remaining;
        System.out.print("enter seconds:");
        totalseconds = sc.nextInt();

        hours=totalseconds/3600;
        remaining = totalseconds%3600;
        minutes = remaining/60;
        seconds = remaining%60;

            System.out.println("time in hours:"+hours);
                        System.out.println("time in minutes:"+minutes);
                                    System.out.println("time in seconds:"+seconds);


            sc.close();

    }
}