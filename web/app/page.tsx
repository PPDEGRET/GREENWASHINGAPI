import Link from "next/link";
import Button from "@/components/Button";

const navLinks = [
  { label: "Dashboard", href: "#" },
  { label: "History", href: "#" },
  { label: "About", href: "#" }
];

export default function LandingPage() {
  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-background-light text-dark-grey">
      <div className="flex grow flex-col">
        <div className="flex flex-1 justify-center px-4 py-5 md:px-10 lg:px-20 xl:px-40">
          <div className="flex max-w-[960px] flex-1 flex-col">
            <header className="flex items-center justify-between whitespace-nowrap border-b border-neutral-grey/30 px-4 py-3 sm:px-6 lg:px-10">
              <div className="flex items-center gap-4 text-dark-grey">
                <div className="size-6 text-primary">
                  <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M13.8261 17.4264C16.7203 18.1174 20.2244 18.5217 24 18.5217C27.7756 18.5217 31.2797 18.1174 34.1739 17.4264C36.9144 16.7722 39.9967 15.2331 41.3563 14.1648L24.8486 40.6391C24.4571 41.267 23.5429 41.267 23.1514 40.6391L6.64374 14.1648C8.00331 15.2331 11.0856 16.7722 13.8261 17.4264Z"
                      fill="currentColor"
                    ></path>
                    <path
                      clipRule="evenodd"
                      d="M39.998 12.236C39.9944 12.2537 39.9875 12.2845 39.9748 12.3294C39.9436 12.4399 39.8949 12.5741 39.8346 12.7175C39.8168 12.7597 39.7989 12.8007 39.7813 12.8398C38.5103 13.7113 35.9788 14.9393 33.7095 15.4811C30.9875 16.131 27.6413 16.5217 24 16.5217C20.3587 16.5217 17.0125 16.131 14.2905 15.4811C12.0012 14.9346 9.44505 13.6897 8.18538 12.8168C8.17384 12.7925 8.16216 12.767 8.15052 12.7408C8.09919 12.6249 8.05721 12.5114 8.02977 12.411C8.00356 12.3152 8.00039 12.2667 8.00004 12.2612C8.00004 12.261 8 12.2607 8.00004 12.2612C8.00004 12.2359 8.0104 11.9233 8.68485 11.3686C9.34546 10.8254 10.4222 10.2469 11.9291 9.72276C14.9242 8.68098 19.1919 8 24 8C28.8081 8 33.0758 8.68098 36.0709 9.72276C37.5778 10.2469 38.6545 10.8254 39.3151 11.3686C39.9006 11.8501 39.9857 12.1489 39.998 12.236ZM4.95178 15.2312L21.4543 41.6973C22.6288 43.5809 25.3712 43.5809 26.5457 41.6973L43.0534 15.223C43.0709 15.1948 43.0878 15.1662 43.104 15.1371L41.3563 14.1648C43.104 15.1371 43.1038 15.1374 43.104 15.1371L43.1051 15.135L43.1065 15.1325L43.1101 15.1261L43.1199 15.1082C43.1276 15.094 43.1377 15.0754 43.1497 15.0527C43.1738 15.0075 43.2062 14.9455 43.244 14.8701C43.319 14.7208 43.4196 14.511 43.5217 14.2683C43.6901 13.8679 44 13.0689 44 12.2609C44 10.5573 43.003 9.22254 41.8558 8.2791C40.6947 7.32427 39.1354 6.55361 37.385 5.94477C33.8654 4.72057 29.133 4 24 4C18.867 4 14.1346 4.72057 10.615 5.94478C8.86463 6.55361 7.30529 7.32428 6.14419 8.27911C4.99695 9.22255 3.99999 10.5573 3.99999 12.2609C3.99999 13.1275 4.29264 13.9078 4.49321 14.3607C4.60375 14.6102 4.71348 14.8196 4.79687 14.9689C4.83898 15.0444 4.87547 15.1065 4.9035 15.1529C4.91754 15.1762 4.92954 15.1957 4.93916 15.2111L4.94662 15.223L4.95178 15.2312ZM35.9868 18.996L24 38.22L12.0131 18.996C12.4661 19.1391 12.9179 19.2658 13.3617 19.3718C16.4281 20.1039 20.0901 20.5217 24 20.5217C27.9099 20.5217 31.5719 20.1039 34.6383 19.3718C35.082 19.2658 35.5339 19.1391 35.9868 18.996Z"
                      fill="currentColor"
                      fillRule="evenodd"
                    ></path>
                  </svg>
                </div>
                <h2 className="text-xl font-bold leading-tight tracking-[-0.015em]">LeafCheck</h2>
              </div>
              <div className="hidden flex-1 justify-end gap-8 md:flex">
                <div className="flex items-center gap-9">
                  {navLinks.map((item) => (
                    <Link
                      key={item.label}
                      href={item.href}
                      className="text-sm font-medium leading-normal text-dark-grey"
                    >
                      {item.label}
                    </Link>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button variant="secondary">Login</Button>
                  <Button>Sign Up</Button>
                </div>
              </div>
              <div className="md:hidden">
                <button className="text-dark-grey">
                  <span className="material-symbols-outlined">menu</span>
                </button>
              </div>
            </header>
            <main className="flex flex-col gap-10 py-10 md:gap-16 md:py-16">
              <div className="flex flex-col items-center gap-6 px-4 text-center">
                <h1 className="text-4xl font-black leading-tight tracking-[-0.033em] text-dark-grey md:text-5xl">
                  Upload an ad — get a greenwashing risk analysis.
                </h1>
                <p className="max-w-2xl text-base font-normal leading-normal text-dark-grey md:text-lg">
                  Our AI analyzes your marketing materials to identify potential greenwashing risks and provides a detailed report.
                </p>
              </div>
              <div className="flex flex-col p-4">
                <div className="flex flex-col items-center gap-6 rounded-xl border-2 border-dashed border-neutral-grey/50 px-6 py-14">
                  <span className="material-symbols-outlined text-5xl text-primary">upload_file</span>
                  <div className="flex max-w-[480px] flex-col items-center gap-2">
                    <p className="max-w-[480px] text-center text-lg font-bold leading-tight tracking-[-0.015em] text-dark-grey">
                      Drag & drop a file here or browse your files.
                    </p>
                    <p className="max-w-[480px] text-center text-sm font-normal leading-normal text-neutral-grey">
                      Our AI will analyze your ad for greenwashing.
                    </p>
                  </div>
                  <Button>Browse Files</Button>
                </div>
              </div>
              <div className="flex flex-col gap-10 px-4 py-10 @container">
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                  <div className="flex flex-1 flex-col items-start gap-4 rounded-xl border border-neutral-grey/30 bg-background-light p-6 text-left">
                    <div className="text-primary">
                      <span className="material-symbols-outlined text-3xl">assessment</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <h2 className="text-lg font-bold leading-tight text-dark-grey">Understand Your Score</h2>
                      <p className="text-sm font-normal leading-normal text-neutral-grey">
                        Get a clear and concise risk score for your ad, with a detailed breakdown of the factors that influenced the score.
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-1 flex-col items-start gap-4 rounded-xl border border-neutral-grey/30 bg-background-light p-6 text-left">
                    <div className="text-primary">
                      <span className="material-symbols-outlined text-3xl">auto_awesome</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <h2 className="text-lg font-bold leading-tight text-dark-grey">AI-Powered Insights</h2>
                      <p className="text-sm font-normal leading-normal text-neutral-grey">
                        Our advanced AI analyzes your ad&apos;s text and imagery to provide you with actionable insights and recommendations.
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-1 flex-col items-start gap-4 rounded-xl border border-neutral-grey/30 bg-background-light p-6 text-left">
                    <div className="text-primary">
                      <span className="material-symbols-outlined text-3xl">workspace_premium</span>
                    </div>
                    <div className="flex flex-col gap-1">
                      <h2 className="text-lg font-bold leading-tight text-dark-grey">Go Premium</h2>
                      <p className="text-sm font-normal leading-normal text-neutral-grey">
                        Unlock advanced features like detailed reports, historical analysis, and competitive benchmarking.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </main>
            <footer className="border-t border-neutral-grey/30 px-4 py-8 md:px-10">
              <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
                <div className="text-sm text-neutral-grey">© 2024 LeafCheck. All rights reserved.</div>
                <div className="flex items-center gap-6">
                  <Link className="text-sm text-neutral-grey hover:text-dark-grey" href="#">
                    Terms of Service
                  </Link>
                  <Link className="text-sm text-neutral-grey hover:text-dark-grey" href="#">
                    Privacy Policy
                  </Link>
                </div>
                <div className="flex gap-4 text-neutral-grey">
                  <Link className="hover:text-dark-grey" href="#" aria-label="Twitter">
                    <svg
                      className="feather feather-twitter"
                      fill="none"
                      height="24"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      width="24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"></path>
                    </svg>
                  </Link>
                  <Link className="hover:text-dark-grey" href="#" aria-label="LinkedIn">
                    <svg
                      className="feather feather-linkedin"
                      fill="none"
                      height="24"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      width="24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                      <rect height="12" width="4" x="2" y="9"></rect>
                      <circle cx="4" cy="4" r="2"></circle>
                    </svg>
                  </Link>
                  <Link className="hover:text-dark-grey" href="#" aria-label="Facebook">
                    <svg
                      className="feather feather-facebook"
                      fill="none"
                      height="24"
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      width="24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path>
                    </svg>
                  </Link>
                </div>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}
