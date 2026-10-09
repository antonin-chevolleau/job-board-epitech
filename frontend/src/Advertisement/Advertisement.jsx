import style from './Advertisement.module.css'
function Advertisement({job_title, location, create_at, short_description, contract_type}) {
    return (
        <>
            <div className={style.div}>
                <p className={style.job_title}>{job_title} - {location}</p>
                <p className={style.date_creation}>{create_at}</p>
                <p>{short_description}</p>
                <p>{contract_type}</p>
                <div className={style.div_button}>
                    <button className={style.button}>View More</button>
                </div>
                
            </div>
        </>
    )
}
export default Advertisement